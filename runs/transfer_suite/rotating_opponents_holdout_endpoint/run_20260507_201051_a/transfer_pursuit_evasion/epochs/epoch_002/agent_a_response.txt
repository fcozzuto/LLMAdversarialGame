def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    self_pos = observation.get("self_position", [0, 0])
    opp_pos = observation.get("opponent_position", [0, 0])
    self_role = (observation.get("self_role", "") or "").lower()
    obstacles = observation.get("obstacles", []) or []

    sx, sy = int(self_pos[0]), int(self_pos[1])
    px, py = int(opp_pos[0]), int(opp_pos[1])
    ox = {tuple(o) for o in obstacles}

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    is_pursuer = ("purs" in self_role) or ("chase" in self_role) or ("hunter" in self_role)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = None
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        nx = clamp(nx, 0, w - 1)
        ny = clamp(ny, 0, h - 1)
        if (nx, ny) in ox:
            continue

        d = cheb(nx, ny, px, py)
        # If we're pursuer: minimize distance; if evader: maximize distance.
        primary = d if not is_pursuer else -d

        # Secondary: stay safe from obstacles (prefer farther from nearest obstacle).
        if ox:
            md = 10**9
            for (oxx, oyy) in ox:
                dd = cheb(nx, ny, oxx, oyy)
                if dd < md: md = dd
        else:
            md = 999

        # Tertiary: deterministic tie-breaker favoring progress away/toward opponent along axes.
        prog = abs(nx - px) + abs(ny - py)
        # Avoid "oscillation" preference: slight bias to not stay unless best.
        stay_pen = 1 if (dx == 0 and dy == 0) else 0

        key = (primary, md if not is_pursuer else -md, prog, -stay_pen)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    if best_move is None:
        return [0, 0]
    return best_move