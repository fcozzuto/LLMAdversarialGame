def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    role = (observation.get("self_role") or "").lower()
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))
    deltas = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def adj_obs(x, y):
        s = 0
        for dx, dy in deltas[:-1]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obs:
                s += 1
        return s

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    # Escape/Intercept heuristics with deterministic scoring over legal moves.
    # Pursuer: minimize distance; strongly avoid moves that reduce escape options for opponent poorly.
    # Evader: maximize distance; avoid moving into tight obstacle clusters (reduce chance of being cornered).
    best_score = None
    best_move = (0, 0)
    target_first = ox if (sx + sy) % 2 == 0 else oy  # deterministic tie-bias
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = manh(nx, ny, ox, oy)
        ao = adj_obs(nx, ny)
        # extra safety: prefer positions with more legal neighboring squares
        neigh_open = 0
        for ddx, ddy in deltas[:-1]:
            tx, ty = nx + ddx, ny + ddy
            if valid(tx, ty):
                neigh_open += 1
        if "pursuer" in role:
            # If capture is possible (d==0), take it.
            score = d
            # Avoid stepping into obstacle tightness that can stall capture.
            score += 2.0 * ao
            # Prefer moves that increase opponent constrainedness: fewer open neighbors near target.
            # Approximate with open neighbors count around opponent's current location.
            opp_open = 0
            for ddx, ddy in deltas[:-1]:
                tx, ty = ox + ddx, oy + ddy
                if valid(tx, ty):
                    opp_open += 1
            score += 0.5 * (opp_open - neigh_open)  # smaller is better for pursuer if opponent is more constrained
            score += 0.01 * ((nx + ny) % 3)  # tiny deterministic tie-break
            if best_score is None or score < best_score:
                best_score = score
                best_move = (dx, dy)
        else:
            # Evader
            # Avoid immediate capture and maximize distance.
            score = -d
            # Strongly avoid tight obstacle areas (being cornered).
            score -= 0.9 * ao
            # Prefer more open neighboring moves (escape routes).
            score += 0.2 * neigh_open
            # If opponent is on parity bias, slightly favor moving away along that axis.
            score += 0.01 * ((target_first == ox and (nx - sx) != 0) or (target_first == oy and (ny - sy) != 0))
            # Deterministic tie-break
            score += -0.0001 * ((nx + 2 * ny) % 5)
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)

    # If all moves were invalid (should be rare), stay put.
    return [int(best_move[0]), int(best_move[1])]