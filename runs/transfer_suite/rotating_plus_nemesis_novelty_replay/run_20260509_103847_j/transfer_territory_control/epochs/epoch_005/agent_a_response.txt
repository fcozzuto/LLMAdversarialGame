def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unT = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    center_x, center_y = w // 2, h // 2
    dirs = [(0, 0), (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy

        # Bonuses for claiming/contesting; prefer approaching opponent and grid center.
        cell_bonus = 0
        if (nx, ny) in unT:
            cell_bonus += 30
        if (nx, ny) in opT and (nx, ny) not in selfT:
            cell_bonus += 40

        # Encourage front progression toward opponent.
        dist_op = manh(nx, ny, ox, oy)
        dist_ctr = manh(nx, ny, center_x, center_y)

        # Small penalty for staying inside our territory too long.
        own_pen = -5 if (nx, ny) in selfT else 0

        val = cell_bonus + own_pen - 1.0 * dist_op - 0.15 * dist_ctr

        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]