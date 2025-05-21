-- whitelist_bot/server.lua
local whitelistEnabled = false
local whitelistedIPs = {}

-- Load whitelist from file
function loadWhitelist()
    local file = LoadResourceFile(GetCurrentResourceName(), 'whitelist.json')
    if file then
        local data = json.decode(file)
        whitelistEnabled = data.enabled
        whitelistedIPs = data.ips
        print(('[IP Whitelist] Loaded - Status: %s'):format(whitelistEnabled and 'ENABLED' or 'DISABLED'))
    else
        print('[IP Whitelist] Error: whitelist.json not found')
    end
end

-- Check player IP on connection
AddEventHandler('playerConnecting', function(name, setKickReason, deferrals)
    local playerIP = GetPlayerEndpoint(source)
    
    if whitelistEnabled and playerIP then
        if not table.contains(whitelistedIPs, playerIP) then
            setKickReason('Your IP is not whitelisted on this server.')
            CancelEvent()
            print(('[IP Whitelist] Blocked connection from %s (IP: %s)'):format(name, playerIP))
        end
    end
end)

-- Helper function to check if table contains value
function table.contains(table, value)
    for _, v in pairs(table) do
        if v == value then
            return true
        end
    end
    return false
end

-- Watch for file changes
Citizen.CreateThread(function()
    local lastModified = 0
    while true do
        Citizen.Wait(5000) -- Check every 5 seconds
        
        local filePath = GetResourcePath(GetCurrentResourceName()) .. '/whitelist.json'
        local modTime = GetFileModTime(filePath)
        
        if modTime > lastModified then
            lastModified = modTime
            loadWhitelist()
            print('[IP Whitelist] Whitelist file updated - reloading')
        end
    end
end)

-- Initial load
Citizen.CreateThread(function()
    loadWhitelist()
end)