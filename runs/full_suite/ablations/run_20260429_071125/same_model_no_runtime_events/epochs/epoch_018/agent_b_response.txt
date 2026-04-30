def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            if "pos" in r and r["pos"] is not None and len(r["pos"]) >= 2:
                resources.append((int(r["pos"][0]), int(r["pos"][1])))
            elif "x" in r and "y" in r and r["x"] is not None and r["y"] is not None:
                resources.append((int(r["x"]), int(r["y"])))

    def cheb(a, b, c, d):
        ax = a - c
        if ax < 0: ax = -ax
        ay = b - d
        if ay < 0: ay = -ay
        return ax if ax >= ay else ay

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources or not valid(sx, sy):
        return [0, 0]

    resources = [rp for rp in resources if valid(rp[0], rp[1]) or rp == (sx, sy)]
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Choose the resource where we have the biggest relative advantage (opp farther than us).
        best_target_adv = -10**18
        best_own_d = 10**9
        best_opp_d = 10**9
        for rx, ry in resources:
            od = cheb(ox, oy, rx, ry)
            nd = cheb(nx, ny, rx, ry)
            adv = od - nd
            if adv > best_target_adv or (adv == best_target_adv and nd < best_own_d) or (adv == best_target_adv and nd == best_own_d and od < best_opp_d):
                best_target_adv = adv
                best_own_d = nd
                best_opp_d = od

        # Evaluate: minimize our distance to the chosen target and, secondarily, keep opponent farther.
        score = (-best_own_d * 10) + (best_opp_d * 2)
        # Immediate pickup preference: if stepping onto any resource, strongly boost.
        if (nx, ny) in set(resources):
            score += 10**6
        # Small penalty for moving away from the closest resource overall.
        closest_now = min(cheb(ox, oy, rx, ry) for rx, ry in resources)
        closest_us_now = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        score += (closest_now - closest_us_now)  # helps if we keep pace while still pushing advantage

        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]