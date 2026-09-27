import { describe,expect,it } from 'vitest';
import { render,screen } from '@testing-library/react';
import { Badge,DemoBanner } from '../src/components/ui';

describe('NWIS UI',()=>{it('shows demo disclosure',()=>{render(<DemoBanner/>);expect(screen.getByText(/DEMO DATA/)).toBeInTheDocument();});it('renders status badge',()=>{render(<Badge tone="green">ACTIVE</Badge>);expect(screen.getByText('ACTIVE')).toBeInTheDocument();});});
