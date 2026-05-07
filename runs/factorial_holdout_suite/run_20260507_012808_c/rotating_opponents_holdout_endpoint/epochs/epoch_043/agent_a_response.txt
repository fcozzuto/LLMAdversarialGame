def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def move_valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best = None
    for dx, dy in moves:
        nx = sx + dx
        ny = sy + dy
        if not move_valid(nx, ny):
            nx, ny = sx, sy
        # choose target resource that this move would race best
        best_adv = None
        best_self_t = None
        for rx, ry in resources:
            self_t = cheb(nx, ny, rx, ry)
            opp_t = cheb(ox, oy, rx, ry)
            adv = self_t - opp_t
            if best_adv is None or adv < best_adv or (adv == best_adv and self_t < best_self_t):
                best_adv = adv
                best_self_t = self_t
        on_res = 1 if (nx, ny) in obstacles else 0
        if any((nx, ny) == (rx, ry) for rx, ry in resources):
            on_res = 1
        # maximize: reach earlier than opponent, then closer; big bonus for landing on a resource
        score = (on_res * 1000000) + (-best_adv * 1000) + (-best_self_t)
        if best is None or score > best[0]:
            best = (score, dx, dy)

    return [best[1], best[2]]