def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None
        ti = int(observation.get("turn_index", 0) or 0)
        for cx, cy in corners:
            if (cx, cy) in obstacles:
                continue
            d = abs(cx - sx) + abs(cy - sy)
            key = (d, (cx + 3 * cy + ti) % 11)
            if best is None or key < best[0]:
                best = (key, cx, cy)
        return [0, 0] if best is None else [int(best[1] > sx) - int(best[1] < sx), int(best[2] > sy) - int(best[2] < sy)]

    def better_key(cell):
        cx, cy = cell
        sd = abs(cx - sx) + abs(cy - sy)
        od = abs(cx - ox) + abs(cy - oy)
        # Prefer targets where we are closer than opponent; then prefer shorter self distance
        return (sd - od, sd, (cx * 7 + cy * 13 + int(observation.get("turn_index", 0) or 0)) % 17)

    resources.sort(key=better_key)
    tx, ty = resources[0]

    # Choose a step that reduces our distance to target and avoids obstacles
    dirs = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if dx == 0 and dy == 0:
                continue
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                nd = abs(tx - nx) + abs(ty - ny)
                # small secondary bias to also move away from opponent
                od = abs(tx - (ox + dx)) + abs(ty - (oy + dy))
                dirs.append((nd, -od, dx, dy))
    # Also allow staying if all moves are bad
    dirs.sort()
    if dirs:
        return [dirs[0][2], dirs[0][3]]
    return [0, 0]