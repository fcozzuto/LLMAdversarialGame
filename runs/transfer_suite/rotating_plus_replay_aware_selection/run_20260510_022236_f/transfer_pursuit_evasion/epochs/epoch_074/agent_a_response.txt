def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role) or ("flee" in role)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def blocked(x, y):
        return (x, y) in obstacles or not (0 <= x < w and 0 <= y < h)

    def neighbor_block_count(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if blocked(x + dx, y + dy):
                    c += 1
        return c

    def best_target_corner_score(x, y):
        # For evader: prefer being far from opponent while also steering to a farthest corner.
        # For pursuer: prefer moving toward the closest corner to reduce evader escape space.
        if not corners:
            return 0
        if is_evader:
            return max(abs(x - cx) + abs(y - cy) for cx, cy in corners)
        else:
            return -min(abs(x - cx) + abs(y - cy) for cx, cy in corners)

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        d = abs(nx - ox) + abs(ny - oy)
        nb = neighbor_block_count(nx, ny)

        if is_evader:
            # Maximize distance; penalize getting boxed in; slight corner bias.
            val = d * 10 - nb * 3 + best_target_corner_score(nx, ny) * 0.1
        else:
            # Minimize distance; penalize boxed in; corner bias in opposite direction.
            val = (-d) * 10 - nb * 3 + best_target_corner_score(nx, ny) * 0.1

        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]