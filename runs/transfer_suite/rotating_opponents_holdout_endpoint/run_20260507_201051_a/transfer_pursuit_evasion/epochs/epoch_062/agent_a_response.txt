def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role") or "").lower()
    am_pursuer = ("purs" in self_role) and ("evad" not in self_role)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def corner_score(x, y, want_far):
        best = 0 if want_far else 10**9
        for cx, cy in corners:
            d = md(x, y, cx, cy)
            if want_far:
                if d > best: best = d
            else:
                if d < best: best = d
        return best

    obs_list = list(obstacles)
    def obs_pen(x, y):
        if (x, y) in obstacles:
            return 10_000_000
        if not obs_list:
            return 0
        best = 10**9
        for px, py in obs_list:
            d = abs(x - px) + abs(y - py)
            if d < best: best = d
        if best <= 0: return 10_000_000
        if best == 1: return 1200
        if best == 2: return 260
        if best == 3: return 80
        return 0

    best_move = (0, 0)
    if am_pursuer:
        best_val = 10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): continue
            val = md(nx, ny, ox, oy) + obs_pen(nx, ny)
            # tie-break: prefer larger progress towards closest corner (more forcing edges)
            val += 0.01 * corner_score(nx, ny, want_far=False)
            if val < best_val:
                best_val = val
                best_move = (dx, dy)
    else:
        best_val = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): continue
            # primary: maximize distance
            val = md(nx, ny, ox, oy)
            # secondary: drift to farthest corner deterministically
            val += 0.05 * corner_score(nx, ny, want_far=True)
            # tertiary: avoid obstacles locally
            val -= 0.6 * obs_pen(nx, ny)
            if val > best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]