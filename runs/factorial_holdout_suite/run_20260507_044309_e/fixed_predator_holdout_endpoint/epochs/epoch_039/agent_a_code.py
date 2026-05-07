def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

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

    # Pick a target resource with best "reach advantage" from current position.
    best_rx, best_ry = resources[0]
    best_margin, best_selfd = -10**9, 10**9
    for rx, ry in resources:
        selfd = cheb(sx, sy, rx, ry)
        oppd = cheb(ox, oy, rx, ry)
        margin = oppd - selfd
        if margin > best_margin or (margin == best_margin and selfd < best_selfd):
            best_margin, best_selfd = margin, selfd
            best_rx, best_ry = rx, ry

    # If opponent is closer or equal, still move to a resource that keeps the margin highest next step.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        # Prefer positions that immediately increase (oppd - selfd) and reduce self distance to target.
        cur_selfd = cheb(nx, ny, best_rx, best_ry)
        cur_oppd = cheb(ox, oy, best_rx, best_ry)
        margin = cur_oppd - cur_selfd

        # Small obstacle-aware penalty: discourage moving next to obstacles (deterministic local proxy).
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if inside(tx, ty) and (tx, ty) in obstacles:
                    adj_obs += 1

        # Secondary: if margin is tied, prefer reducing distance to the opponent (resource-denier pressure).
        opp_seek = -cheb(nx, ny, ox, oy)

        val = margin * 1000 - cur_selfd * 3 + opp_seek - adj_obs * 5
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]