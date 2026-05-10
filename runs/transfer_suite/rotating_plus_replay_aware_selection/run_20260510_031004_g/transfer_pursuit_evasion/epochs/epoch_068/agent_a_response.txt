def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    is_pursuer = None
    if "purs" in self_role:
        is_pursuer = True
    elif "evad" in self_role:
        is_pursuer = False
    if is_pursuer is None:
        if "evad" in opp_role:
            is_pursuer = False
        elif "purs" in opp_role:
            is_pursuer = True
    if is_pursuer is None:
        is_pursuer = True

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    def manhattan(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        d = manhattan(nx, ny, ox, oy)
        if is_pursuer:
            # chase while discouraging stepping "into" walls
            score = -d
            # minor bias toward reducing both axes (more direct pursuit)
            score += -abs(nx - ox) - abs(ny - oy) * 0.01
        else:
            # evade: maximize distance
            score = d
            # bias toward moving away in the dominant direction
            score += (nx - ox) * (1 if nx >= ox else -1) * 0.001
            score += (ny - oy) * (1 if ny >= oy else -1) * 0.001

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]
        elif score == best_score:
            # deterministic tie-break: prefer staying if equal advantage, else smallest dx then dy
            if best == [0, 0] and [dx, dy] != [0, 0]:
                continue
            if best != [0, 0] and [dx, dy] == [0, 0]:
                best = [dx, dy]
            elif [dx, dy] < best:
                best = [dx, dy]

    return best if best is not None else [0, 0]