def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for c in observation.get("obstacles", []) or []:
        if c is not None and len(c) >= 2 and c[0] is not None and c[1] is not None:
            obstacles.add((int(c[0]), int(c[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    self_set = set(tuple(map(int, p)) for p in (observation.get("self_territory", []) or []))
    opp_set = set(tuple(map(int, p)) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set(tuple(map(int, p)) for p in (observation.get("unclaimed_cells", []) or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    best = (0, 0)
    best_sc = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in self_set:
            base = 1.2
        elif (nx, ny) in opp_set:
            base = 3.4  # likely flip
        elif (nx, ny) in unclaimed:
            base = 2.6
        else:
            base = 1.0

        dist_center = abs(nx - cx) + abs(ny - cy)
        dist_to_opp = abs(nx - ox) + abs(ny - oy)
        # Favor center pressure while also approaching opponent
        sc = base * 10 - dist_center * 0.55 - dist_to_opp * 0.18

        # Nudge toward nearest unclaimed if any exist (local, deterministic)
        if unclaimed:
            best_u = None
            for ux, uy in unclaimed:
                d = abs(ux - nx) + abs(uy - ny)
                if best_u is None or d < best_u:
                    best_u = d
            sc -= best_u * 0.05 if best_u is not None else 0

        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    return [int(best[0]), int(best[1])]