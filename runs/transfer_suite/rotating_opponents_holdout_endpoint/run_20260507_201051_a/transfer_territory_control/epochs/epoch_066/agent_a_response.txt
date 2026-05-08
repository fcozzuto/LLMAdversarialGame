def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_cells = set()
    for p in (observation.get("self_territory") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            self_cells.add((int(p[0]), int(p[1])))

    opp_cells = set()
    for p in (observation.get("opponent_territory") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_cells.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for p in (observation.get("unclaimed_cells") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best_move = [0, 0]
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        base = 0
        if (nx, ny) in unclaimed:
            base = 6
        elif (nx, ny) in opp_cells:
            base = 7
        elif (nx, ny) in self_cells:
            base = 2
        else:
            base = 1

        # Avoid walking into opponent's advance while pushing edges away from them.
        dist_opp = abs(nx - ox) + abs(ny - oy)
        dist_center = abs(nx - cx) + abs(ny - cy)
        val = base * 100 + dist_opp * 3 - dist_center

        # Small determinism jitter from coordinates (no randomness).
        val += (nx * 31 + ny * 17) * 1e-6

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move