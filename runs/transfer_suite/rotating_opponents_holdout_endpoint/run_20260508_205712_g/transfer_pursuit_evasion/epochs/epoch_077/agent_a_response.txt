def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    sr = str(observation.get("self_role") or "").lower()
    self_evader = any(k in sr for k in ("evader", "escape", "runner"))
    # If self is evader, opponent is likely pursuer, otherwise likely evader.
    opp_is_pursuer = not self_evader

    def greedy_step(px, py, tx, ty, pursuer):
        best = None
        best_move = (0, 0)
        # Deterministic tie-break: iterate moves order, keep first best.
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if not inb(nx, ny):
                continue
            d = manh(nx, ny, tx, ty)
            val = d if pursuer else -d
            if best is None or val < best if pursuer else val > best:
                best = val
                best_move = (dx, dy)
        return best_move

    best_score = None
    best_move = (0, 0)

    for dx0, dy0 in moves:
        nx0, ny0 = sx + dx0, sy + dy0
        if not inb(nx0, ny0):
            continue
        # Opponent reacts based on their assumed role at this next state.
        # If opponent is pursuer: it moves toward our next position; else it moves away.
        odx, ody = greedy_step(ox, oy, nx0, ny0, opp_is_pursuer)
        nxo, nyo = ox + odx, oy + ody
        if not inb(nxo, nyo):
            nxo, nyo = ox, oy

        d_after = manh(nx0, ny0, nxo, nyo)
        if d_after == 0:
            score = -10.0 if self_evader else 10.0
        else:
            # Evader wants to maximize distance; pursuer wants to minimize.
            score = (-d_after) if not self_evader else (d_after)

            # Small corner bias for evader (avoid getting sandwiched), inverse for pursuer.
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            bc = min(manh(nx0, ny0, cx, cy) for cx, cy in corners)
            # Evader prefers staying far from closest corner; pursuer prefers closer.
            score += (-bc) if not self_evader else (bc)

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx0, dy0)

    return [int(best_move[0]), int(best_move[1])]