def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    if w < 2 or h < 2 or not isinstance(sp, (list, tuple)) or not isinstance(op, (list, tuple)) or len(sp) < 2 or len(op) < 2:
        return [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles") or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "pursuer").lower()
    is_evader = role == "evader"

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy
    def neigh_block(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacles:
                c += 1
        return c
    def corner_target(ex, ey):
        # choose corner that maximizes Chebyshev distance from (ex,ey)
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None
        for cx, cy in corners:
            d = cheb(cx, cy, ex, ey)
            if best is None or d > best[0]:
                best = (d, cx, cy)
        return best[1], best[2]

    tx, ty = (corner_target(ox, oy) if is_evader else (ox, oy))
    # If evader: run away from pursuer toward farthest corner; if pursuer: chase exact opponent position.
    best = None
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            continue
        d_opp = cheb(nx, ny, ox, oy)
        d_tar = cheb(nx, ny, tx, ty)
        # Prefer moves that reduce distance to target as pursuer; increase distance from opponent as evader.
        if is_evader:
            # primary: maximize distance from opponent, secondary: approach far corner, tertiary: avoid obstacles
            score = (-d_opp, d_tar, -neigh_block(nx, ny))
        else:
            # primary: minimize distance to opponent/target, secondary: avoid obstacles (stay in open), tertiary: avoid being adjacent to obstacles
            score = (d_opp, d_tar, neigh_block(nx, ny))
        if best is None or score < best:
            best = score
            best_move = [dx, dy]
    return best_move