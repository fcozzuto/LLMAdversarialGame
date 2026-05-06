def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def rep_pos(p):
        if isinstance(p, dict):
            q = p.get("position")
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                return (q[0], q[1])
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            return (p[0], p[1])
        return None

    rpos = []
    for r in resources:
        q = rep_pos(r)
        if q and inb(q[0], q[1]) and q not in blocked:
            rpos.append(q)
    if not rpos:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def king_dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    def best_value_from(pos):
        best = None
        for r in rpos:
            sd = king_dist(pos, r)
            od = king_dist((ox, oy), r)
            val = od - sd
            if best is None or val > best[0] or (val == best[0] and sd < best[1]):
                best = (val, sd)
        return best

    best_move = (None, None, None)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        val, sd = best_value_from((nx, ny))
        # Small deterministic tiebreakers to avoid oscillations: prefer moves that reduce distance to opponent if tied.
        pod = king_dist((nx, ny), (ox, oy))
        cand = (val, -sd, -pod, dx, dy)
        if best_move[0] is None or cand > best_move:
            best_move = cand

    return [int(best_move[3]), int(best_move[4])]