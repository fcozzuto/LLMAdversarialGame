def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

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

    if not resources:
        return [0, 0]

    best = (-10**18, 10**9, 0, 0)  # (margin, selfd, nx, ny)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            # If invalid, engine keeps us in place; simulate that by evaluating staying.
            nx, ny = sx, sy

        # Find best margin against opponent after moving to (nx, ny).
        top_margin = -10**18
        top_selfd = 10**9
        for rx, ry in resources:
            selfd = cheb(nx, ny, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            margin = oppd - selfd
            if margin > top_margin or (margin == top_margin and selfd < top_selfd):
                top_margin, top_selfd = margin, selfd

        if top_margin > best[0] or (top_margin == best[0] and top_selfd < best[1]):
            best = (top_margin, top_selfd, nx, ny)

    bx, by = best[2], best[3]
    return [bx - sx, by - sy]