def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)
    opp_pos = observation.get("opponent_position", None)
    ox, oy = (opp_pos if isinstance(opp_pos, (list, tuple)) and len(opp_pos) == 2 else (None, None))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not selfT and (sx, sy) not in selfT:
        selfT.add((sx, sy))

    if unclaimed:
        # Prefer frontier unclaimed cells adjacent to our territory (fewer steps, expands our control).
        frontier = []
        for (x, y) in selfT:
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if (nx, ny) in unclaimed and inb(nx, ny) and (nx, ny) not in obstacles:
                    # Slight preference away from opponent (helps prevent edge fight).
                    od = abs(ox - nx) + abs(oy - ny) if ox is not None else 0
                    frontier.append((od, abs(nx - sx) + abs(ny - sy), (nx, ny)))
        candidates = frontier if frontier else [(0, abs(ux - sx) + abs(uy - sy), (ux, uy)) for (ux, uy) in unclaimed]
        candidates.sort(key=lambda t: (-t[0], t[1], t[2][1], t[2][0]))
        tx, ty = candidates[0][2]
    else:
        # If no unclaimed, capture by pressing toward opponent territory.
        if opp_pos is None or ox is None:
            return [0, 0]
        tx, ty = ox, oy

    best = (10**9, 10**9, 10**9, 0, 0)  # score, dist, penalty, dx, dy
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Primary objective: reduce distance to target.
        dist = abs(tx - nx) + abs(ty - ny)
        d0 = abs(tx - sx) + abs(ty - sy)
        improvement = d0 - dist
        # Secondary: avoid walking into opponent territory unless it helps (small penalty).
        opp_pen = 0
        if (nx, ny) in oppT:
            # discourage; but allow diagonal/close pressure by lowering penalty if moving closer
            opp_pen = 2 if improvement <= 0 else 0
        # Tertiary: keep moves stable deterministically
        penalty = opp_pen + (1 if (dx == 0 and dy == 0) else 0)
        score = (-improvement, dist, penalty, dx, dy)
        if score < best:
            best = score

    return [int(best[3]), int(best[4])]