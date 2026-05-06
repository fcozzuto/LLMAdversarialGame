def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # Build deterministic ordered move list
    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    # If no resources, drift to improve relative positioning: move toward opponent
    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            return [dx, dy]
        return [0, 0]

    # Pick best move by "win the race" to resources and penalize giving opponent a closer start
    best_move = [0, 0]
    best_val = -10**18
    self_pos = (sx, sy)
    opp_pos = (ox, oy)

    # Pre-rank resources for determinism and speed
    ranked = sorted(resources, key=lambda t: (cheb(self_pos, t), t[0], t[1]))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        ns = (nx, ny)

        # Consider only top few closest resources to reduce noise and keep deterministic
        val = 0
        for i in range(min(6, len(ranked))):
            r = ranked[i]
            d_self_now = cheb(ns, r)
            d_opp_now = cheb(opp_pos, r)

            d_self_cur = cheb(self_pos, r)
            d_opp_cur = cheb(opp_pos, r)

            # Encourage getting to resources faster than opponent, and improving over current move
            race = (d_opp_now - d_self_now)
            improve = (d_self_cur - d_self_now)

            # If resource is already "won" soon, give more weight; else still keep pressure
            urgency = (7 - i)  # higher for closer-ranked resources
            # Penalize steps that move you away (negative improve) and reduce race advantage
            val += urgency * (3.0 * race + 1.2 * improve)

            # Tie-breaker preference: keep move slightly toward that resource
            val += 0.01 * (-cheb(ns, r))

            # Discourage moves that help the opponent in a practical sense: opponent chasing same resource
            # (opponent position fixed this turn, so approximate via relative race gap only)
            val -= 0.15 * max(0, -race)

        # Deterministic tie-break on move itself
        if val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]