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
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        remaining = observation.get("remaining_resource_count")
        if isinstance(remaining, int) and remaining <= 0:
            resources = []

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18

    opp_scores = observation.get("scores")
    my_score = None
    op_score = None
    if isinstance(opp_scores, dict):
        my_score = opp_scores.get("self", opp_scores.get("player", None))
        op_score = opp_scores.get("opponent", opp_scores.get("enemy", None))
    elif isinstance(opp_scores, (list, tuple)) and len(opp_scores) >= 2:
        my_score, op_score = opp_scores[0], opp_scores[1]
    if not isinstance(my_score, (int, float)):
        my_score = 0
    if not isinstance(op_score, (int, float)):
        op_score = 0

    chase_resource = my_score < op_score

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_opp = abs(nx - ox) + abs(ny - oy)
        if resources:
            d_res = min(dist((nx, ny), r) for r in resources)
        else:
            d_res = 0 if chase_resource else 999999

        val = 0
        if chase_resource:
            val += -10 * d_res
            val += -1 * d_opp
        else:
            val += -3 * d_res
            val += -10 * d_opp

        if val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]