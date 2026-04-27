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

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1,  0), (0,  0), (1,  0),
            (-1,  1), (0,  1), (1,  1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Core heuristic: move toward closest resource if available; otherwise approach opponent
    best_dx = 0
    best_dy = 0
    best_score = None

    if resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            dist = min((man(nx, ny, rx, ry) for (rx, ry) in resources), default=999)
            score = -dist
            if best_score is None or score > best_score:
                best_score = score
                best_dx, best_dy = dx, dy
    else:
        # No resources: pressure toward center slightly while staying near opponent
        centerx, centery = w // 2, h // 2
        to_center = -man(sx + 0, sy + 0, centerx, centery)
        to_opp = -man(sx, sy, ox, oy)
        # move that reduces distance to center more than approaching opponent
        if to_center >= to_opp:
            # pick move toward center if legal
            dx = centerx - sx
            dy = centery - sy
            # normalize to -1,0,1
            ndx = 0 if dx == 0 else (1 if dx > 0 else -1)
            ndy = 0 if dy == 0 else (1 if dy > 0 else -1)
            if legal(sx + ndx, sy + ndy):
                best_dx, best_dy = ndx, ndy
            else:
                # fallback toward opponent
                dx = ox - sx
                dy = oy - sy
                ndx = 0 if dx == 0 else (1 if dx > 0 else -1)
                ndy = 0 if dy == 0 else (1 if dy > 0 else -1)
                if legal(sx + ndx, sy + ndy):
                    best_dx, best_dy = ndx, ndy
                else:
                    best_dx, best_dy = 0, 0
        else:
            dx = ox - sx
            dy = oy - sy
            ndx = 0 if dx == 0 else (1 if dx > 0 else -1)
            ndy = 0 if dy == 0 else (1 if dy > 0 else -1)
            if legal(sx + ndx, sy + ndy):
                best_dx, best_dy = ndx, ndy
            else:
                best_dx, best_dy = 0, 0

    # Ensure final move is legal; if not, stay
    nx, ny = sx + best_dx, sy + best_dy
    if not legal(nx, ny):
        best_dx, best_dy = 0, 0

    return [best_dx, best_dy]