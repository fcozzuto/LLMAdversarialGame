def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    # Fallback: if resources isn't a list of positions, try remaining_resource_count only
    if not resources:
        resources = [(w // 2, h // 2)]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best = None
    best_sc = -10**18

    # Prefer capturing/approaching nearest resource while avoiding opponent when close
    close_op = ((sx - ox) * (sx - ox) + (sy - oy) * (sy - oy)) <= 4

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_opp = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        # nearest resource distance
        d_res = min((nx - rx) * (nx - rx) + (ny - ry) * (ny - ry) for rx, ry in resources)
        sc = -d_res
        if close_op:
            sc += d_opp * 0.5
        else:
            # slightly encourage getting closer to opponent if not too risky
            sc -= d_opp * 0.05
        if best is None or sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    if best is not None:
        return best

    # If all moves blocked, stay
    return [0, 0]