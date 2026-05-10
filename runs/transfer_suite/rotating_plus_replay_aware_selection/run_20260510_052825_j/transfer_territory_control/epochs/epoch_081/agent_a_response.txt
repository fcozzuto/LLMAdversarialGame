def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    x, y = observation.get("self_position", (0, 0))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)
    opp_pos = observation.get("opponent_position", None)
    ox, oy = opp_pos if isinstance(opp_pos, (list, tuple)) and len(opp_pos) == 2 else (None, None)

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def edge_dist(cx, cy):
        return min(cx, w - 1 - cx, cy, h - 1 - cy)

    def opp_reach_dist(nx, ny):
        if ox is None:
            return 999
        return abs(nx - ox) + abs(ny - oy)

    dirs = (-1, 0, 1)
    best = (None, -10**18)
    for dx in dirs:
        for dy in dirs:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            gain = 0
            if (nx, ny) in unclaimed:
                gain += 10.0
            if (nx, ny) in selfT:
                gain += 1.0
            if (nx, ny) in oppT:
                gain += 6.5  # flipping reward
            # Prefer expanding toward open space while staying away from opponent for safety
            gain += (3.0 - 0.2 * edge_dist(nx, ny))
            gain -= 0.9 * (opp_reach_dist(nx, ny))
            # If we're not already near our territory, slightly discourage moving into opponent territory
            if (nx, ny) in oppT:
                neigh_ours = 0
                for adx in dirs:
                    for ady in dirs:
                        if adx == 0 and ady == 0:
                            continue
                        tx, ty = nx + adx, ny + ady
                        if inb(tx, ty) and (tx, ty) in selfT:
                            neigh_ours += 1
                gain -= 1.5 if neigh_ours == 0 else 0.0
            if gain > best[1]:
                best = ([dx, dy], gain)

    if best[0] is not None:
        return best[0]

    # Fallback: allow staying still or any valid move
    for dx in dirs:
        for dy in dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
    return [0, 0]