export type NetworkDictItem = { id: string; name: string; region: string };
export type StoreDictItem = { id: string; name: string; networkId: string; city: string };
export type RegionDictItem = { id: string; name: string };

export type Dictionaries = {
  networks: NetworkDictItem[];
  stores: StoreDictItem[];
  regions: RegionDictItem[];
};
