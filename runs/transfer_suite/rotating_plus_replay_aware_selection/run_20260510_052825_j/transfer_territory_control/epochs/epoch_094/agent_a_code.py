def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)
    opp_pos = observation.get("opponent_position", None)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Local expansion heuristic
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    my_adj = set()
    for (tx, ty) in selfT:
        for dx, dy in dirs:
            nx, ny = tx + dx, ty + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                my_adj.add((nx, ny))
    my_adj.add((sx, sy))

    def local_value(nx, ny):
        if not inb(nx, ny) or (nx, ny) in obstacles:
            return -10**9
        gain = 0.0
        if (nx, ny) in unclaimed:
            gain += 10.0
        if (nx, ny) in oppT:
            gain += 6.0
        if (nx, ny) in selfT:
            gain += 1.5

        # Count how much this move helps us "frontier-out"
        frontier = 0
        for dx, dy in dirs:
            ax, ay = nx + dx, ny + dy
            if inb(ax, ay) and (ax, ay) not in obstacles:
                if (ax, ay) in unclaimed:
                    frontier += 1
                elif (ax, ay) in oppT:
                    frontier += 0.5
                elif (ax, ay) in selfT:
                    frontier += 0.25
        gain += 2.2 * frontier

        # Prefer moving to cells adjacent to our territory, otherwise chase nearby unclaimed
        if (nx, ny) in my_adj:
            gain += 2.5
        else:
            if unclaimed:
                d = min(abs(nx - ux) + abs(ny - uy) for (ux, uy) in unclaimed)
                gain -= 0.35 * d

        # Mild opposition pressure: don't give up progress to chase too far
        if opp_pos and isinstance(opp_pos, (list, tuple)) and len(opp_pos) == 2:
            ox, oy = opp_pos
            md = abs(nx - ox) + abs(ny - oy)
            gain += 0.08 * (-md)  # closer to opponent mildly
        return gain

    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        v = local_value(nx, ny)
        if v > best[0]:
            best = (v, dx, dy)

    return [int(best[1]), int(best[2])]