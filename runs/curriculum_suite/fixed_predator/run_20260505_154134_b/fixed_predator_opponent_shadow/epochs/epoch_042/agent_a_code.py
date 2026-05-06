def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_resource_adv(px, py):
        if not resources:
            return -10**9
        best = -10**9
        for cx, cy in resources:
            self_d = cheb(px, py, cx, cy)
            opp_d = cheb(ox, oy, cx, cy)
            # prefer making ourselves at least as close as opponent, while pushing contested cells
            adv = (opp_d - self_d)
            # discourage going too slow; deterministic tie breaks
            key = adv * 100 + (-self_d) * 2 + (-(cx + 31 * cy) if adv == best else 0)
            if key > best:
                best = key
        return best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        hit = (nx, ny) in obs
        # if hit, expect engine to keep us in place; incorporate obstacle penalty
        px, py = (sx, sy) if hit else (nx, ny)
        score = best_resource_adv(px, py)
        # additional penalty to avoid entering obstacles even if engine would keep us
        if hit:
            score -= 2000
        # break ties deterministically towards smaller dx/dy sum magnitude, then lexicographic
        score += - (abs(dx) + abs(dy)) * 0.01
        if score > best_score + 1e-12:
            best_score = score
            best_move = [dx, dy]
        elif abs(score - best_score) <= 1e-12:
            if [dx, dy] < best_move:
                best_move = [dx, dy]
    return best_move