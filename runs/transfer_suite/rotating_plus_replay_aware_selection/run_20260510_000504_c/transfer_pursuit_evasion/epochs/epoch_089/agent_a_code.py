def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in self_role) or ("escape" in self_role) or ("runner" in self_role) or ("flee" in self_role)

    def dist2(x, y, a, b):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if is_evader:
        target_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    else:
        target_corner = min(corners, key=lambda c: dist2(c[0], c[1], ox, oy))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        d_opp = dist2(nx, ny, ox, oy)
        d_corner = dist2(nx, ny, target_corner[0], target_corner[1])
        man_opp = abs(nx - ox) + abs(ny - oy)
        man_corner = abs(nx - target_corner[0]) + abs(ny - target_corner[1])

        # Small tie-breaker: prefer moves that don't "clip" into dead ends behind obstacles.
        deadpen = 0
        for adx, ady in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            tx, ty = nx + adx, ny + ady
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) in obstacles:
                deadpen += 1

        if is_evader:
            # Maximize distance from pursuer, also head toward farthest corner from pursuer, avoid tight dead regions.
            val = (d_opp * 3.0) - (d_corner * 0.02) + (man_corner * 0.01) - (deadpen * 0.12) - (man_opp * 0.001)
        else:
            # Minimize distance to evader, prefer moves that bring us closer to capture-favorable corner while avoiding dead regions.
            val = (-d_opp * 3.0) + (-d_corner * 0.01) - (man_corner * 0.002) - (deadpen * 0.12) + (man_opp * 0.001)

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]