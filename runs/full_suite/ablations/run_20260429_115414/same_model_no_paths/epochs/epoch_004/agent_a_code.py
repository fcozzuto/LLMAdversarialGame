def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((o[0], o[1]) for o in observation.get("obstacles", []))
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    def obs_pen(x, y):
        best = 999
        for ox2, oy2 in obstacles:
            d = cheb(x, y, ox2, oy2)
            if d < best: best = d
        if best == 999:
            return 0
        return max(0, 3 - best) * 2  # penalty when near obstacles
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = [(dx, dy) for dx, dy in dirs if inb(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]
    if not resources:
        tx, ty = (w // 2, h // 2)
        bestm = None
        bestv = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            v = cheb(nx, ny, tx, ty) + obs_pen(nx, ny) * 10
            if bestv is None or v < bestv:
                bestv = v
                bestm = (dx, dy)
        return [bestm[0], bestm[1]]
    opp_bottleneck = cheb(ox, oy, w - 1 - sx, h - 1 - sy)  # deterministic coarse anchor
    bestm = None
    bestv = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        self_near = []
        # choose best resource for this move using "uncontested advantage" primary
        for rx, ry in resources:
            dm = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # If we're behind, favor resources with large opponent distance; if ahead, favor closeness.
            advantage = do - dm
            contested = do - (dm + 1)
            if contested < 0:
                score = advantage * 120 - dm * 6 + do * 10
            else:
                score = advantage * 160 + (10 - dm) * 12 - do * 2
            # Add opponent-direction pressure so we don't all chase same line
            score += (rx + ry - (ox + oy)) * 1
            self_near.append((score, dm, do, rx, ry))
        self_near.sort(reverse=True)
        top_score, dm, do, rx, ry = self_near[0]
        # Strongly discourage moves that increase opponent's advantage over the top resource
        stay_dm = cheb(sx, sy, rx, ry)
        stay_adv = do - stay_dm
        new_adv = do - dm
        delta_adv = new_adv - stay_adv
        v = -top_score - delta_adv * 80 + obs_pen(nx, ny) * 50 - min(opp_bottleneck, do) * 0.1
        if bestv is None or v < bestv:
            bestv = v
            bestm = (dx, dy)
    return [bestm[0], bestm[1]]