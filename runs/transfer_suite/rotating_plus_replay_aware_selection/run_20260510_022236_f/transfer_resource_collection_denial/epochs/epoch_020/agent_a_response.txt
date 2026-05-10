def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def eval_state(px, py):
        best = None
        for rx, ry in resources:
            rx, ry = int(rx), int(ry)
            if not inb(rx, ry):
                continue
            self_d = cheb(px, py, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            lead = opp_d - self_d
            cand = (lead, -self_d, -opp_d, rx, ry)
            if best is None or cand > best:
                best = cand
        if best is None:
            return (0, 10**9, 0)
        return best[:3]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obs_set:
                continue
            moves.append((dx, dy))
    if not moves:
        moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    best_move = None  # (score, dx, dy) where higher is better deterministically
    cur_best = eval_state(sx, sy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        score = eval_state(nx, ny)
        # Prefer improvement; if tie, prefer closer to opponent (more denial), then lexicographic dx,dy
        cand = (score[0] - cur_best[0], score[1], score[2], -dx, -dy, dx, dy)
        if best_move is None or cand > best_move[0]:
            best_move = (cand, dx, dy)

    return [int(best_move[1]), int(best_move[2])]