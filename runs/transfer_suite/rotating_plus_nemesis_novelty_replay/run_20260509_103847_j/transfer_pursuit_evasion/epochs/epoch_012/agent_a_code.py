def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def sgn(a): return 0 if a == 0 else (1 if a > 0 else -1)

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def corner_bias(x, y):
        # deterministic slight preference to corners to reduce escape freedom
        best = 0
        for cx, cy in corners:
            best = max(best, -(abs(cx - x) + abs(cy - y)))
        return best

    best_move = (0, 0)
    best_score = -10**18
    # Deterministic tie-breaker ordering favors diagonal approach then cardinal then stay
    order = [(-1, -1), (1, 1), (-1, 1), (1, -1), (-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]

    for odx, ody in order:
        nx, ny = sx + odx, sy + ody
        if not inb(nx, ny):
            continue

        # Predict opponent move: maximize distance from our candidate, avoid illegal cells
        best_opp = None
        best_opp_d = -10**18
        for pdx, pdy in deltas:
            tx, ty = ox + pdx, oy + pdy
            if not inb(tx, ty):
                continue
            d = dist2(tx, ty, nx, ny)
            # discourage stepping into capture by us (prefer moves that avoid equality)
            cap_avoid = 1 if (tx == nx and ty == ny) else 0
            d2 = d - 1e6 * cap_avoid
            # mild bias to keep moving in roughly away direction (evasion_wall_runner feel)
            d2 += 0.01 * (sgn(ox - nx) * pdx + sgn(oy - ny) * pdy)
            # mild bias to corners (consistent deterministic behavior)
            d2 += 0.001 * corner_bias(tx, ty)
            if d2 > best_opp_d:
                best_opp_d = d2
                best_opp = (tx, ty)

        if best_opp is None:
            continue
        tx, ty = best_opp

        # Score our move: immediate capture is best; else minimize predicted distance
        if nx == tx and ny == ty:
            score = 10**12
        else:
            score = -dist2(nx, ny, tx, ty)
            # additional tie-break: move toward center line away from nearest obstacle to avoid being boxed
            # (lightweight and deterministic)
            score += 0.0001 * (corner_bias(nx, ny))

        if score > best_score:
            best_score = score
            best_move = (odx, ody)

    return [int(best_move[0]), int(best_move[1])]