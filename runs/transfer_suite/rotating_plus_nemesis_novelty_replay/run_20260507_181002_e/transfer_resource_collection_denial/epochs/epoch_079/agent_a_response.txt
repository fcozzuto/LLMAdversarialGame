def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [sx, sy])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def step_score(x, y):
        # Find best resource to contest; reward taking closest advantage.
        best = -10**9
        for rx, ry in resources:
            sd = manh(x, y, rx, ry)
            od = manh(ox, oy, rx, ry)
            # Strongly prefer resources where we are closer; discourage those where opponent is closer.
            # Add urgency: smaller distances are better.
            val = (od - sd) * 6 + (30 - sd) - (5 if od < sd else 0)
            if sd == 0:
                val += 500
            best = max(best, val)
        return best

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy
            dx, dy = 0, 0

        v1 = step_score(nx, ny)

        # Tiny 2-ply lookahead for robustness (opponent assumed greedy-nearest; we ignore opponent move for determinism).
        # Simulate our best next action from (nx,ny) one more step.
        best_next = -10**18
        for ddx, ddy in moves:
            nnx, nny = nx + ddx, ny + ddy
            tdx, tdy = ddx, ddy
            if not (0 <= nnx < w and 0 <= nny < h) or (nnx, nny) in obs:
                nnx, nny = nx, ny
                tdx, tdy = 0, 0
            cand = step_score(nnx, nny) - (1 if (tdx, tdy) == (0, 0) else 0)
            if cand > best_next:
                best_next = cand
        v = v1 + 0.35 * best_next

        # Deterministic tie-break: prefer smaller move lexicographically toward (0,0), then prefer toward positive x then y.
        if v > best_val:
            best_val = v
            best_move = (dx, dy)
        elif v == best_val:
            if (abs(dx) + abs(dy), -dx, -dy) < (abs(best_move[0]) + abs(best_move[1]), -best_move[0], -best_move[1]):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]