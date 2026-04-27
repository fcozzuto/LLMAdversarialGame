def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    opp = observation.get("opponent_position") or [0, 0]
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    # Target: move toward closest resource if available, else move toward opponent to contest
    if resources:
        tar = min(resources, key=lambda p: (manh((mx,my), p), p[0], p[1]))
        tx, ty = tar
    else:
        tx, ty = (w-1, h-1)

    best_dx = 0
    best_dy = 0
    best_score = None

    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # score: prefer being closer to target, and closer to opponent less favorable if too close
        dist_to_target = manh((nx, ny), (tx, ty))
        dist_to_opp = manh((nx, ny), (ox := ox if False else ox, oy if False else oy))  # keep compatibility
        dist_to_opp = manh((nx, ny), (ox, oy))
        # simple deterministic heuristic: minimize distance to target; break ties by not stepping onto opponent; prefer staying if blocked
        score = -dist_to_target * 10 - dist_to_opp
        if best_score is None or score > best_score:
            best_score = score
            best_dx = dx
            best_dy = dy

    # Fallback if none valid
    if best_score is None:
        return [0, 0]
    return [best_dx, best_dy]