def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sp = observation.get("self_position")
    op = observation.get("opponent_position")
    if w < 1 or h < 1 or not isinstance(sp, (list, tuple)) or not isinstance(op, (list, tuple)) or len(sp) < 2 or len(op) < 2:
        return [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = (observation.get("self_role") or "pursuer").lower()
    opp_role = (observation.get("opponent_role") or "evader").lower()

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def step(pos, d):
        nx, ny = pos[0] + d[0], pos[1] + d[1]
        if not inb(nx, ny) or (nx, ny) in obstacles:
            return pos
        return (nx, ny)

    def obs_pen(x, y):
        if (x, y) in obstacles:
            return 10**9
        if not obstacles:
            return 0
        p = 0
        for ax, ay in obstacles:
            dist = abs(x - ax) + abs(y - ay)
            if dist == 0:
                return 10**9
            if dist == 1:
                p += 6
            elif dist == 2:
                p += 2
        return p

    def evader_move(from_pos, purs_pos):
        best = None
        bx = besty = 0
        for d in deltas:
            nx, ny = step(from_pos, d)
            score = cheb(nx, ny, purs_pos[0], purs_pos[1]) - 0.35 * obs_pen(nx, ny)
            if best is None or score > best:
                best = score
                bx, by = nx, ny
        return (bx, by)

    def pursuer_move(from_pos, ev_pos):
        best = None
        bx = by = 0
        for d in deltas:
            nx, ny = step(from_pos, d)
            score = -cheb(nx, ny, ev_pos[0], ev_pos[1]) - 0.25 * obs_pen(nx, ny)
            if best is None or score > best:
                best = score
                bx, by = nx, ny
        return (bx, by)

    if self_role == "evader" or opp_role == "pursuer":
        new_ev = evader_move((sx, sy), (ox, oy))
        return [int(new_ev[0] - sx), int(new_ev[1] - sy)]

    # Pursuer: greedy chase with one-step prediction for evader
    predicted_ev = evader_move((ox, oy), (sx, sy))
    new_pos = pursuer_move((sx, sy), predicted_ev)
    return [int(new_pos[0] - sx), int(new_pos[1] - sy)]