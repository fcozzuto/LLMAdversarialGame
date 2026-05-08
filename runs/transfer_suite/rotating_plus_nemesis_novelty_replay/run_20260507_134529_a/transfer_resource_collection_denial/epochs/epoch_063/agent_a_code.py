def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obs

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        best = (-10**9, (0, 0))
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                nx, ny = sx, sy
            v = cheb(nx, ny, ox, oy)
            if v > best[0] or (v == best[0] and (dx, dy) < best[1]):
                best = (v, (dx, dy))
        return [best[1][0], best[1][1]]

    contested = [r for r in resources if abs(r[1] - oy) <= 1]
    cand = contested if contested else resources

    best = (-10**18, 10**9, (0, 0))
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy

        best_diff = -10**18
        best_selfd = 10**9
        for rx, ry in cand:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            diff = od - sd
            if diff > best_diff or (diff == best_diff and sd < best_selfd):
                best_diff = diff
                best_selfd = sd

        # Prefer making us closer to the most contested resource we can beat.
        # Tie-break deterministically by lexicographic move.
        key = (best_diff, -best_selfd, -dx, -dy)
        best_key = (best[0], best[1] * -1, -best[2][0], -best[2][1])
        if key > best_key:
            best = (best_diff, best_selfd, (dx, dy))

    return [best[2][0], best[2][1]]