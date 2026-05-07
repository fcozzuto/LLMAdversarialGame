def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best = None  # (margin, -selfd, move_index, dx, dy)
    for mi, (dxm, dym) in enumerate(moves):
        nx, ny = sx + dxm, sy + dym
        if not inside(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        top_margin = -10**18
        top_selfd = 10**9
        for rx, ry in resources:
            selfd = cheb(nx, ny, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            margin = oppd - selfd
            if margin > top_margin or (margin == top_margin and selfd < top_selfd):
                top_margin = margin
                top_selfd = selfd

        cand = (top_margin, -top_selfd, mi, dxm, dym)
        if best is None or cand > best:
            best = cand

    return [best[3], best[4]]