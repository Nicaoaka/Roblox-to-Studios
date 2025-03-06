_=[[

NOTES
	It is assumed that there are no repeats
	ALL Script-generated objects are temporary,
		Persistent after: Copy / Paste Into At Original Locaiton

]]


SAME_SIDE_AS_FEATURED_1 = false





_=[[ Get/Make Temporary Folders ]]

local folderName = "confirmedParts"
local confirmedPartsFolder = workspace:FindFirstChild(folderName)
if not confirmedPartsFolder then
	confirmedPartsFolder = Instance.new("Folder")
	confirmedPartsFolder.Name = folderName
	confirmedPartsFolder.Parent = workspace
	warn("Please copy and paste the " .. confirmedPartsFolder.Name .. " folder to make it persistent.")
end
folderName = "NewParts"
local newPartsFolder = workspace:FindFirstChild(folderName)
if not newPartsFolder then
	newPartsFolder = Instance.new("Folder")
	newPartsFolder.Name = folderName
	newPartsFolder.Parent = workspace
end
folderName = "NewPartsCHECK"
local checkFolder = workspace:FindFirstChild(folderName)
if not checkFolder then
	checkFolder = Instance.new("Folder")
	checkFolder.Name = folderName
	checkFolder.Parent = workspace
end



_=[[ HTTP Polling GET from API/localhost/VSCode ]]
local HttpService = game:GetService("HttpService")
local URL = "http://127.0.0.1:8000/get"
local response
local parts_csv

-- Use pcall in case something goes wrong
local success, response = pcall(function()
	response = HttpService:GetAsync(URL) -- JSON
	parts_csv = HttpService:JSONDecode(response) -- Table
end)


-- Did our request fail or our JSON fail to parse?
if not success then
	warn(response)
	return false
end



_=[[ Decode CSV Table ]]
-- Function to parse a single CSV line and convert values to their appropriate types
local function parseCSVLine(line)
	local values = {} -- Table to store converted values

	-- Loop through each value in the CSV line, splitting by commas
	for value in line:gmatch("([^,]+)") do
		-- Convert "True" and "False" to boolean values
		if value == "True" then
			table.insert(values, true)
		elseif value == "False" then
			table.insert(values, false)
			-- Convert numbers (integers and decimals) to numeric type
		elseif tonumber(value) then
			table.insert(values, tonumber(value))
			-- Keep everything else as a string
		else
			table.insert(values, value)
		end
	end

	return values -- Return the parsed and converted values as a table (list)
end

-- Function to process multiple CSV lines
local function decodeCSV(csvLines)
	local decoded = {} -- Table to store all parsed CSV rows

	-- Loop through each CSV line and decode it using parseCSVLine
	for _, line in ipairs(csvLines) do
		-- Remove the last two characters if they are newline characters
		if line:sub(-2) == "\r\n" then
			line = line:sub(1, -3) -- Remove the last two characters
		elseif line:sub(-1) == "\n" then
			line = line:sub(1, -2) -- Remove the last character
		end

		table.insert(decoded, parseCSVLine(line))
	end

	return decoded -- Return the fully parsed CSV data as a table of tables (2D array)
end

-- Table{string}
local parts = decodeCSV(parts_csv)



_=[[ Place The Parts (in Workspace/folders) ]]

for i, data in parts do
	
	-- Default values for each field
	local defaults = {
		true,
		true,
		255, 255, 255,
		Enum.Material["Plastic"],
		0,
		Enum.SurfaceType["Studs"],
		0,
		0, 0, 0, -- position
		1, 1, 1, -- size
		0, 0, 0, -- orientation
		Enum.PartType["Block"]
	}
	local fieldNames = {
		'CanCollide',
		'CastShadow',
		'Color_R', 'Color_G', 'Color_B',
		'Material',
		'Reflectance',
		'Surface',
		'Transparency',
		'Position_X', 'Position_Y', 'Position_Z',
		'Size_X', 'Size_Y', 'Size_Z',
		'Orientation_X', 'Orientation_Y', 'Orientation_Z',
		'Shape'
	}
	
	local allCertain = true
	local part = Instance.new("Part")
	if data[19] == 0 then
		part = Instance.new("TrussPart")
		print("Placing Truss")
	end
	part.Name = "Part"

	-- Function to validate and return the correct value
	local function validateType(index, value, expectedType)
		if typeof(value) == expectedType then
			return value
		else
			allCertain = false
			local script = Instance.new("Script")
			script.Name = fieldNames[index] .. " = '" .. value .."'"
			script.Parent = part
			return defaults[index] -- Return default value
		end
	end
	
	local function validateEnum(index, value, enum)
		local enumNames = {}
		-- Check if value is a key in enum
		for _, enumItem in ipairs(enum:GetEnumItems()) do
			if value == enumItem.Name  then
				return enum[value]
			end
		end
		allCertain = false
		local script = Instance.new("Script")
		script.Name = fieldNames[index] .. " = '" .. value .."'"
		script.Parent = part
		return defaults[index] -- Return default value
	end

	-- Assign values with validation
	part.CanCollide = validateType(1, data[1], "boolean")
	part.CastShadow = validateType(2, data[2], "boolean")
	part.Color = Color3.fromRGB(
		validateType(3, data[3], "number"),
		validateType(4, data[4], "number"),
		validateType(5, data[5], "number")
	)
	part.Material = validateEnum(6, data[6], Enum.Material)
	part.Reflectance = validateType(7, data[7], "number")

	local surfaceType = validateEnum(8, data[8], Enum.SurfaceType)
	part.TopSurface = surfaceType
	part.BottomSurface = surfaceType
	part.FrontSurface = surfaceType
	part.BackSurface = surfaceType
	part.LeftSurface = surfaceType
	part.RightSurface = surfaceType

	part.Transparency = validateType(9, data[9], "number")
	
	
	
	_=[[ OC to Studios ]]
	_={	[[SAME SIDE Featured 1]],
		-1,  1,  1,		[[position]],
		 1,  1,  1,		[[size]],
		 1,  1,  1,		[[orientation]],
	}
	_={ [[OPPOSITE SIDE Featured 1]],
		-1,  1,  1,		[[position]],
		1,  1,  1,		[[size]],
		1,  -1,  1,		[[orientation]],
	}

	
	part.Position = Vector3.new(
		validateType(10, data[10], "number") * -1,
		validateType(11, data[11], "number"),
		validateType(12, data[12], "number")
	)
	part.Size = Vector3.new(
		validateType(13, data[13], "number"),
		validateType(14, data[14], "number"),
		validateType(15, data[15], "number")
	)
	
	-- for wedges / cornerwedge
	local function flipOrientation(n)
		if n > 0 then
			return n - 180
		else
			return n + 180
		end
	end

	if SAME_SIDE_AS_FEATURED_1 then
		part.Orientation = Vector3.new(
			validateType(16, data[16], "number"),
			validateType(17, data[17], "number"),
			validateType(18, data[18], "number")
		)
	else
		part.Orientation = Vector3.new(
			validateType(16, data[16], "number"),
			flipOrientation(validateType(17, data[17], "number")),
			validateType(18, data[18], "number")
		)
	end
	
	if data[19] ~= 0 then -- truss has shape = 0 (int)
		part.Shape = validateEnum(19, data[19], Enum.PartType)
	end

	part.Archivable = true
	part.Anchored = true

	-- Place part in the appropriate folder
	if allCertain then
		part.Parent = newPartsFolder
	else
		part.Parent = checkFolder
	end

	--print("Placed Part# " .. i)
end


