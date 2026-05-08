def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    is_pursuer = ("purs" in role) or ("catch" in role) or ("purs" in opp_role and "evad" not in role)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def neighbors_free(x, y):
        cnt = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if ok(nx, ny):
                    cnt += 1
        return cnt

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            cheb = max(abs(nx - ox), abs(ny - oy))
            free = neighbors_free(nx, ny)
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            far_corner_dist = max(abs(nx - cx) + abs(ny - cy) for cx, cy in corners)
            diag_block = (dx != 0 and dy != 0 and not ok(nx - dx, ny) and not ok(nx, ny - dy))
            candidates.append((nx, ny, dx, dy, cheb, free, far_corner_dist, diag_block))

    if not candidates:
        return [0, 0]

    if is_pursuer:
        # minimize distance; then maximize mobility; then prefer moves that avoid blocking-diagonal slips
        candidates.sort(key=lambda t: (t[4], -t[5], t[7], t[2], t[3]))
    else:
        # maximize distance; then mobility; then drift toward farthest corner
        candidates.sort(key=lambda t: (-t[4], -t[5], -t[6], t[2], t[3]))

    _, _, dx, dy, _, _, _, _ = candidates[0]
    return [int(dx), int(dy)]