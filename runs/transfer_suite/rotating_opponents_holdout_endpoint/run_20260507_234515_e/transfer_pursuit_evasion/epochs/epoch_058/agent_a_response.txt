def choose_move(observation):
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((int(p[0]), int(p[1])))
    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role) or ("escape" in role) or ("runner" in role)
    if ("pursuer" in role) or ("hunter" in role):
        is_evader = False

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    edges = {0, w - 1, w - 1, 0}

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def free(x, y):
        return inside(x, y) and (x, y) not in oset

    def obstacle_penalty(x, y):
        # Penalize moving into tight spots around obstacles
        pen = 0
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            nx, ny = x + dx, y + dy
            if (nx, ny) in oset:
                pen += 3
        return pen

    def edge_preference(x, y):
        # For evader: hug the farthest boundary; for pursuer: cut off to nearest boundary
        dleft = x
        dright = (w - 1) - x
        ddown = y
        dup = (h - 1) - y
        return -min(dleft, dright) if is_evader else min(dleft, dright) + min(ddown, dup)

    def corner_dist_score(x, y):
        return max(md(x, y, cx, cy) for (cx, cy) in corners) if is_evader else min(md(x, y, cx, cy) for (cx, cy) in corners)

    # Wall-runner style: prefer increasing distance and then moving along the best axis towards a corner/edge
    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d_op = md(nx, ny, ox, oy)
        if is_evader:
            # primary: maximize distance; secondary: maximize corner distance; tertiary: keep to edges; penalize obstacle tightness
            val = (d_op * 1000) + (corner_dist_score(nx, ny) * 10) + (edge_preference(nx, ny) * 2) - obstacle_penalty(nx, ny)
            # tiny deterministic bias to break ties: prefer moves that increase one coordinate away from opponent
            val += (1 if (abs(nx - ox) > abs(sx - ox)) else 0) + (1 if (abs(ny - oy) > abs(sy - oy)) else 0) * 0.01
        else:
            # primary: minimize distance; secondary: push toward edges to restrict; avoid obstacles
            val = (-d_op * 1000) + (edge_preference(nx, ny) * 2) + (-obstacle_penalty(nx, ny)) - (corner_dist_score(nx, ny) * 0.01)
        if best is None or val > best_val or (val == best_val and (dx, dy) < best):
            best = (dx, dy)
            best_val = val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]