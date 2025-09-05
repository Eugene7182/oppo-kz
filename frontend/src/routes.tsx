import React from 'react';
import { RouteObject } from 'react-router-dom';
import Layout from './components/Layout';
import Guard from './components/Guard';
import Login from './pages/Login';
import Health from './pages/Health';
import Networks from './pages/Dicts/Networks';
import Stores from './pages/Dicts/Stores';
import PriceUpload from './pages/Price/PriceUpload';
import SkuList from './pages/Price/SkuList';
import Jobs from './pages/Price/Jobs';
import Balances from './pages/Inventory/Balances';
import Adjust from './pages/Inventory/Adjust';
import MovesList from './pages/Moves/MovesList';
import CreateMove from './pages/Moves/CreateMove';
import NetworkSales from './pages/Sales/NetworkSales';
import PromoterSales from './pages/Sales/PromoterSales';
import Reconcile from './pages/Sales/Reconcile';
import Shipments from './pages/Logistics/Shipments';
import InTransit from './pages/Logistics/InTransit';
import MessagesList from './pages/Messages/MessagesList';
import MessageCreate from './pages/Messages/MessageCreate';
import Flags from './pages/Flags/Flags';
import NotFound from './pages/NotFound';

// Application routes
export const routes: RouteObject[] = [
  { path: '/login', element: <Login /> },
  {
    path: '/',
    element: (
      <Guard>
        <Layout />
      </Guard>
    ),
    children: [
      { index: true, element: <Health /> },
      { path: 'dicts/networks', element: <Guard roles={['admin', 'office']}><Networks /></Guard> },
      { path: 'dicts/stores', element: <Guard roles={['admin', 'office']}><Stores /></Guard> },
      { path: 'price/upload', element: <Guard roles={['admin']}><PriceUpload /></Guard> },
      { path: 'price/sku', element: <Guard roles={['admin']}><SkuList /></Guard> },
      { path: 'imports/jobs', element: <Guard roles={['admin']}><Jobs /></Guard> },
      { path: 'inventory/balances', element: <Guard roles={['admin','office','supervisor']}><Balances /></Guard> },
      { path: 'inventory/adjust', element: <Guard roles={['admin','office']}><Adjust /></Guard> },
      { path: 'moves', element: <Guard roles={['admin','office']}><MovesList /></Guard> },
      { path: 'moves/create', element: <Guard roles={['admin','office']}><CreateMove /></Guard> },
      { path: 'sales/network', element: <Guard roles={['admin','office']}><NetworkSales /></Guard> },
      { path: 'sales/promoter', element: <Guard roles={['admin','office','supervisor','promoter']}><PromoterSales /></Guard> },
      { path: 'sales/reconcile', element: <Guard roles={['admin']}><Reconcile /></Guard> },
      { path: 'logistics/shipments', element: <Guard roles={['admin','office']}><Shipments /></Guard> },
      { path: 'logistics/in-transit', element: <Guard roles={['admin','office']}><InTransit /></Guard> },
      { path: 'messages', element: <Guard roles={['admin','office']}><MessagesList /></Guard> },
      { path: 'messages/create', element: <Guard roles={['admin','office']}><MessageCreate /></Guard> },
      { path: 'flags', element: <Guard roles={['admin']}><Flags /></Guard> },
    ],
  },
  { path: '*', element: <NotFound /> },
];
