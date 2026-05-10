def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    # If we are evading, move away; otherwise chase.
    self_role = observation.get("self_role", "") or ""
    evading = ("evad" in self_role.lower())
    tx, ty = ox, oy

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            d = abs(nx - tx) + abs(ny - ty)
            # Prefer fewer obstacles-losing moves; deterministic tie-break by (dx,dy).
            score = (-d if not evading else d, -((nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)))
            candidates.append((score, dx, dy))

    if not candidates:
        return [0, 0]

    # Deterministic selection: max by score, then lexicographic dx/dy (fixed order).
    candidates.sort(key=lambda t: (t[0][0], t[0][1], -t[1], -t[2]), reverse=True)
    return [int(candidates[0][1]), int(candidates[0][2])]