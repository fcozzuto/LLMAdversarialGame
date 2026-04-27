def choose_move(observation):
    turn = int(observation.get("turn_index", 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist(ax, ay, bx, by):
        return max(abs(ax - bx), abs(ay - by))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),  (0, 0),  (0, 1),
             (1, -1),  (1, 0),  (1, 1)]

    # deterministic tie-breaker helpers
    def clamp(x, a, b):
        return max(a, min(b, x))

    best_move = (0, 0)
    best_score = -10**9

    # If there are resources, head to the closest not-occupied resource
    if resources:
        # deterministic: pick resource with minimal (chebyshev distance, rx, ry)
        chosen = None
        best_r = None
        for (rx, ry) in resources:
            d = dist(sx, sy, rx, ry)
            if best_r is None or d < best_r or (d == best_r and (rx < (chosen[0] if chosen else rx) or (rx == (chosen[0] if chosen else rx) and ry < (chosen[1] if chosen else ry)))):
                best_r = d
                chosen = (rx, ry)
        if chosen is not None:
            tx, ty = chosen
            # choose a move that reduces Chebyshev distance to target
            dx = 0
            dy = 0
            if sx < tx: dx = 1
            elif sx > tx: dx = -1
            if sy < ty: dy = 1
            elif sy > ty: dy = -1
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                return [dx, dy]

    # Fallback: move away from opponent if blocked by edge or obstacle; otherwise inch toward center
    dx = 0
    dy = 0
    if sx < ox: dx = -1
    elif sx > ox: dx = 1
    if sy < oy: dy = -1
    elif sy > oy: dy = 1

    # try to reduce proximity to opponent to avoid direct conflict, but keep deterministic
    cand = [(dx, dy), (0,0), (dx, -dy) if dy != 0 else (dx,0), (-dx, dy) if dx != 0 else (0, dy)]
    tried = []
    for mx, my in cand:
        nx, ny = sx + mx, sy + my
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue
        if (nx, ny) == (ox, oy):
            continue
        if legal(nx, ny):
            return [mx, my]
        tried.append((nx, ny))

    # If no safe move found, stay
    return [0, 0]