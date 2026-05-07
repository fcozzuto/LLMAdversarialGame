def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_move = [0, 0]
    best_val = -10**18

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        if resources:
            # Prefer moves that get closer to some resource, especially ones closer to us than opponent.
            val = -10**9
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # Winning pressure: larger (do - ds); tie-breaker: prefer farther from opponent.
                v = (do - ds) * 10 - ds + cheb(ox, oy, rx, ry) * 0.001
                if v > val:
                    val = v
            # Avoid stepping directly into opponent proximity if not improving.
            opp_prox = 1 if cheb(nx, ny, ox, oy) <= 1 else 0
            val -= opp_prox * 2
        else:
            # No resources: move away deterministically.
            dcur = cheb(sx, sy, ox, oy)
            dfut = cheb(nx, ny, ox, oy)
            val = (dfut - dcur) * 10 - dfut
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]