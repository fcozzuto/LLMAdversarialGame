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

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),  (0, 0),  (0, 1),
             (1, -1),  (1, 0),  (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    # Target resources by closest distance, then prefer center-proximity as tie-breaker
    target_list = resources if resources else [(ox, oy)]
    best_move = None
    best_score = None

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0  # center

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # proximity to nearest target
        tscore = 0
        best_tdist = None
        for tx, ty in target_list:
            d = max(abs(nx - tx), abs(ny - ty))
            if best_tdist is None or d < best_tdist:
                best_tdist = d
        tscore -= (best_tdist if best_tdist is not None else 0)

        # center closeness (prefer being near center)
        cdist = max(abs(nx - cx), abs(ny - cy))
        tscore -= cdist * 0.1

        # discourage moving onto opponent's square to avoid immediate capture
        if (nx, ny) == (ox, oy):
            tscore -= 100

        if best_score is None or tscore > best_score:
            best_score = tscore
            best_move = [dx, dy]

    if best_move is None:
        # fallback: move away from opponent if possible, else stay
        fx, fy = sx, sy
        if ox > sx and legal(sx - 1, sy):
            best_move = [-1, 0]
        elif ox < sx and legal(sx + 1, sy):
            best_move = [1, 0]
        elif oy > sy and legal(sx, sy - 1):
            best_move = [0, -1]
        elif oy < sy and legal(sx, sy + 1):
            best_move = [0, 1]
        else:
            best_move = [0, 0]

    return best_move