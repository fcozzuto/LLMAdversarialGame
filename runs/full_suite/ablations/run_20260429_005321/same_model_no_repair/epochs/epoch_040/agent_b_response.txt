def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obs)

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def obstacle_penalty(x, y):
        # Small deterministic penalty for being adjacent to obstacles (encourages safer lanes)
        p = 0
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            nx, ny = x + dx, y + dy
            if (nx, ny) in obs:
                p += 1
        return p

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    if not resources:
        dx = 0 if sx == ox else (1 if ox > sx else -1)
        dy = 0 if sy == oy else (1 if oy > sy else -1)
        if blocked(sx + dx, sy + dy):
            # try any valid move that reduces king distance to opponent
            best = (0, 0)
            bestd = 10**9
            for mdx, mdy in moves:
                nx, ny = sx + mdx, sy + mdy
                if blocked(nx, ny):
                    continue
                d = king_dist(nx, ny, ox, oy)
                if d < bestd:
                    bestd = d
                    best = (mdx, mdy)
            return [best[0], best[1]]
        return [dx, dy]

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue

        # Choose the resource that gives the strongest relative advantage now
        best_for_move = -10**18
        best_selfd = 10**9
        for rx, ry in resources:
            selfd = king_dist(nx, ny, rx, ry)
            oppd = king_dist(ox, oy, rx, ry)
            val = (oppd - selfd) * 1000 - selfd  # prioritize winning contests, then shorter routes
            if val > best_for_move or (val == best_for_move and selfd < best_selfd):
                best_for_move = val
                best_selfd = selfd

        # discourage risky adjacency to obstacles
        best_for_move -= 5 * obstacle_penalty(nx, ny)

        if best_for_move > best_val:
            best_val = best_for_move
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]