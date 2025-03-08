





_=[[

NOTES
	ALL Script-generated objects are temporary.
		They become Persistent after: Copy -> Paste Into At Original Locaiton
	
]]

local DELIMITER = ";"

local FLIP = false

_=[[ Debug Tools ]]

local function rotate_180(orientation)
	return orientation + 180
end
local function inverse(n)
	return -n
end






_=[[ Get/Make Temporary Folders ]]

local folderName = "Confirmed"
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
folderName = "CHECK"
local checkFolder = workspace:FindFirstChild(folderName)
if not checkFolder then
	checkFolder = Instance.new("Folder")
	checkFolder.Name = folderName
	checkFolder.Parent = workspace
end



_=[[ HTTP GET Request from API / localhost / VSCode ]]

local HttpService = game:GetService("HttpService")
local URL = "http://127.0.0.1:8000/get"
local response
local delimited_data

local success, response = pcall(function() -- Use pcall in case something goes wrong
	response = HttpService:GetAsync(URL) -- JSON
	delimited_data = HttpService:JSONDecode(response) -- Table
end)
if not success then
	warn(response)
	return false
end



_=[[ Decode CSV Table ]]

local function split(inputstr, sep)
	if sep == nil then
		sep = "%s"
	end
	local t = {}
	for str in string.gmatch(inputstr, "([^"..sep.."]+)") do
		table.insert(t, str)
	end
	return t
end

local all_part_data = {}
for _, line in ipairs(delimited_data) do
	line = line:sub(1, -2) -- last two characters are \n
	-- Correct Type
	local part_data = {}
	for _, str in ipairs(split(line, DELIMITER)) do
		-- boolean
		if str == "True" then
			table.insert(part_data, true)
		elseif str == "False" then
			table.insert(part_data, false)
			-- int / float
		elseif tonumber(str) then
			table.insert(part_data, tonumber(str))
			-- string
		else
			table.insert(part_data, str)
		end
	end
	table.insert(all_part_data, part_data)
end



_=[[ Place The Parts (in Workspace/folders) ]]

for _, part_data in ipairs(all_part_data) do
	local part = Instance.new(part_data[1])
	part.CanCollide = part_data[2]
	part.CastShadow = part_data[3]
	part.Color = Color3.fromRGB(
		part_data[4], part_data[5], part_data[6]
	)
	part.Material = Enum.Material[part_data[7]]
	part.Reflectance = part_data[8]

	local surfaceType = Enum.SurfaceType[part_data[9]]
	part.TopSurface = surfaceType
	part.BottomSurface = surfaceType
	part.FrontSurface = surfaceType
	part.BackSurface = surfaceType
	part.LeftSurface = surfaceType
	part.RightSurface = surfaceType

	part.Transparency = part_data[10]
	part.Position = Vector3.new(
		part_data[11], part_data[12], part_data[13]
	)
	part.Size = Vector3.new(
		part_data[14], part_data[15], part_data[16]
	)
	if FLIP then
		part.Orientation = Vector3.new(
			part_data[17], rotate_180(part_data[18]), part_data[19]
		)
	else
		part.Orientation = Vector3.new(
			part_data[17], part_data[18], part_data[19]
		)
	end

	if part_data[1] == "TrussPart" then
		part.Style = Enum.Style[part_data[20]]
	else
		part.Shape = Enum.PartType[part_data[20]]
	end

	part.Archivable = true
	part.Anchored = true
	part.Parent = newPartsFolder

	-- Place part in the appropriate folder
	for i, data in ipairs(part_data) do
		if i >= 21 and part_data[i] then
			part.Parent = checkFolder
			local script = Instance.new("Script")
			script.Name = part_data[i]
			script.Parent = part
		end
	end

	print("Placed object at:", part.Position)

end

