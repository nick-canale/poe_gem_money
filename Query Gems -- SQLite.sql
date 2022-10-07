-- SQLite

with GemNames as (select distinct GemName from Gems)

, BuyGems as (
    select GemName, ChaosValue+(20-GemQuality)*1.5 ChaosValue, GemQuality, GemLevel, row_number()over(PARTITION BY GemName ORDER BY ChaosValue+(20-GemQuality)*1.5) rownum
    from Gems a
    where IsCorrupted = 0
    and ListingCount > 10
)
, SellLevel20Gems as (
    select GemName, ChaosValue, ListingCount, GemQuality, GemLevel, row_number()over(PARTITION BY GemName ORDER BY ChaosValue) rownum
    from Gems a
    where GemLevel = 20
    and GemQuality = 20
)
, SellAwakenedGems as (
    select GemName, ChaosValue, ListingCount, GemQuality, GemLevel, row_number()over(PARTITION BY GemName ORDER BY ChaosValue) rownum
    from Gems a
    where GemLevel = 5
    and GemQuality = 20
    and IsAwakened = 1
    and ExceptionalGem = 0
)
, SellExceptionalAwakenedGems as (
    select GemName, ChaosValue, ListingCount, GemQuality, GemLevel, row_number()over(PARTITION BY GemName ORDER BY ChaosValue) rownum
    from Gems a
    where GemLevel = 4
    and IsAwakened = 1
    and ExceptionalGem = 1
)
, SellGemsCorruptWin as (
    select GemName, ChaosValue, ListingCount, GemQuality, GemLevel, row_number()over(PARTITION BY GemName ORDER BY ChaosValue) rownum
    from Gems a
    where GemLevel = 21
    and IsAwakened = 0
    and ExceptionalGem = 0
)

, SellAwakenedGemsCorruptWin as (
    select GemName, ChaosValue, ListingCount, GemQuality, GemLevel, row_number()over(PARTITION BY GemName ORDER BY ChaosValue) rownum
    from Gems a
    where GemLevel = 6
    and IsAwakened = 1
    and ExceptionalGem = 0
)
, SellExceptionalAwakenedGemsCorruptWin as (
    select GemName, ChaosValue, ListingCount, GemQuality, GemLevel, row_number()over(PARTITION BY GemName ORDER BY ChaosValue) rownum
    from Gems a
    where GemLevel = 5
    and IsAwakened = 1
    and ExceptionalGem = 1
)


select a.GemName
, b.ChaosValue BuyPrice
, coalesce(c.ChaosValue, d.ChaosValue, e.ChaosValue) SellPrice
, b.GemLevel BuyGemLevel
, b.GemQuality BuyGemQuality
, coalesce(c.GemLevel, d.GemLevel, e.GemLevel) SellGemLevel
, coalesce(c.ListingCount, d.ListingCount, e.ListingCount) SellListingCount
, coalesce(c.ChaosValue, d.ChaosValue, e.ChaosValue)-b.ChaosValue Profit

, coalesce(f.ChaosValue, g.ChaosValue, h.ChaosValue) SellPriceCorruptWin
, coalesce(f.GemLevel, g.GemLevel, h.GemLevel) SellGemLevelCorruptWin
, coalesce(f.ListingCount, g.ListingCount, h.ListingCount) SellListingCountCorruptWin
, coalesce(f.ChaosValue, g.ChaosValue, h.ChaosValue)-b.ChaosValue ProfitCorruptWin
from GemNames a
inner join BuyGems b
    on a.GemName = b.GemName
    and b.rownum = 1
left outer join Selllevel20Gems c
    on a.GemName = c.GemName
    and c.rownum = 1
left outer join SellAwakenedGems d
    on a.GemName = d.GemName
    and d.rownum = 1
left outer join SellExceptionalAwakenedGems e
    on a.GemName = e.GemName
    and e.rownum = 1
left outer join SellGemsCorruptWin f
    on a.GemName = f.GemName
    and f.rownum = 1
left outer join SellAwakenedGemsCorruptWin g
    on a.GemName = g.GemName
    and g.rownum = 1
left outer join SellExceptionalAwakenedGemsCorruptWin h
    on a.GemName = h.GemName
    and h.rownum = 1
order by coalesce(f.ChaosValue, g.ChaosValue, h.ChaosValue)-b.ChaosValue desc

/*
SELECT a.GemName
, a.ChaosValue BuyPrice
, a.GemLevel BuyGemLevel
, a.GemQuality BuyGemQuality
, a.ListingCount BuyListings
, b.GemLevel SellGemLevel
, b.ChaosValue SellPrice
, b.ListingCount SellListings
, case when a.IsCorrupted = 1 then (b.ChaosValue - a.ChaosValue * 8)*(1/8) else b.ChaosValue - a.ChaosValue end Profit
FROM Gems a
inner join Gems b
    on a.GemName = b.GemName
    and b.GemLevel = 21
    and b.GemQuality = 20
where a.GemLevel <> 20
and a.GemQuality <> 0
order by Profit desc
*/