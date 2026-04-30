def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h
    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))
    def legal(nx, ny):
        return inside(nx, ny) and (nx, ny) not in obstacles

    opp = (ox, oy)
    me = (sx, sy)
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # Avoid immediate collision into opponent
        if (nx, ny) == opp:
            val = -10**9
        else:
            # Target nearest resource (or just continue optimizing toward resources)
            if resources:
                dres = min(dist((nx, ny), r) for r in resources)
            else:
                dres = 0

            # Also avoid being too close to opponent
            dnear_opp = dist((nx, ny), opp)

            # Predict "best escape" for opponent: if our move gives them a very good resource distance advantage, avoid it
            # (cheap approximation: compare current nearest-resource distances)
            if resources:
                cur_me = min(dist(me, r) for r in resources)
                cur_opp = min(dist(opp, r) for r in resources)
                opp_after = 10**9
                for odx, ody in moves:
                    tx, ty = ox + odx, oy + ody
                    if not legal(tx, ty):
                        continue
                    d = min(dist((tx, ty), r) for r in resources)
                    if d < opp_after:
                        opp_after = d
                # Prefer moves that don't let opponent immediately become much closer to resources than us
                adv_pen = max(0, (opp_after - (dres)) - (cur_opp - cur_me))
            else:
                adv_pen = 0

            # Weighted deterministic scoring
            val = -1.8 * dres + 0.95 * dnear_opp - 2.2 * adv_pen

            # If already on a resource, favor staying/collecting
            if resources and (nx, ny) in resources:
                val += 50

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]