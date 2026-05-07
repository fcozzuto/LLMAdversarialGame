def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = (-(10**9), 10**9, 0)  # (margin, self_dist, order)
    best_move = (0, 0)

    for order, (dx, dy) in enumerate(moves):
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        # Choose move by best immediate advantage over opponent toward any remaining resource
        local_margin = -(10**9)
        local_self = 10**9
        for rx, ry in resources:
            sd = king_dist(nx, ny, rx, ry)
            od = king_dist(ox, oy, rx, ry)
            # Encourage being closer than opponent; slight preference for nearer resources.
            margin = od - sd
            if margin > local_margin or (margin == local_margin and sd < local_self):
                local_margin, local_self = margin, sd

        cand = (local_margin, local_self, order)
        if cand[0] > best[0] or (cand[0] == best[0] and (cand[1] < best[1] or (cand[1] == best[1] and cand[2] < best[2]))):
            best = cand
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]