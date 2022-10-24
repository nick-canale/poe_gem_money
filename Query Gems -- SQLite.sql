SELECT a.GemName
    , a.ChaosValue BuyPrice
    , a.ListingCount BuyListings
    , b.GemLevel SellGemLevel
    , b.ChaosValue SellPrice
    , b.ListingCount SellListings
	, b.IsCorrupted SellingCorrupted
	, c.experience
    , cast(case when b.iscorrupted = 1 then (b.ChaosValue - a.ChaosValue)*(1.0/8.0) else b.ChaosValue - a.ChaosValue end / ((c.experience * 1.0) / 341000000.0) as int) AdjustedProfit
from Gems a
left outer join gems b
	on a.gemname = b.gemname
	and a.id <> b.id
	and b.ListingCount > 4
left outer join gemexp c
	on replace(replace(replace(a.gemname,'Phantasmal ',''),'Anomalous ',''),'Divergent ','') = c.GemName
where a.ListingCount > 10
and a.iscorrupted = 0
order by AdjustedProfit desc
