def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_move = [0, 0]
    best_val = None

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue

            # If we land on a resource, prioritize it heavily.
            landed = 0
            for tx, ty in resources:
                if tx == nx and ty == ny:
                    landed = 1
                    break

            # Race advantage: pick the resource where we expect to beat the opponent after this move.
            our_best_adv = -10**9
            our_best_sd = 10**9
            opp_best_adv = -10**9
            opp_best_sd = 10**9

            for tx, ty in resources:
                sd = cheb(nx, ny, tx, ty)
                od = cheb(ox, oy, tx, ty)
                adv = od - sd
                if adv > our_best_adv or (adv == our_best_adv and sd < our_best_sd):
                    our_best_adv = adv
                    our_best_sd = sd

                # Also account for denial threat: opponent's advantage if we let them choose.
                # Use same formula but treat it as opponent targeting (swap roles).
                opp_adv = sd - od  # = -(adv)
                if opp_adv > opp_best_adv or (opp_adv == opp_best_adv and od < opp_best_sd):
                    opp_best_adv = opp_adv
                    opp_best_sd = od

            # Combine: prioritize guaranteed pick, then maximize our advantage,
            # while minimizing how good it is for the opponent (denial resistance).
            val = (landed, our_best_adv, -opp_best_adv, -our_best_sd, -opp_best_sd)
            if best_val is None or val > best_val:
                best_val = val
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]