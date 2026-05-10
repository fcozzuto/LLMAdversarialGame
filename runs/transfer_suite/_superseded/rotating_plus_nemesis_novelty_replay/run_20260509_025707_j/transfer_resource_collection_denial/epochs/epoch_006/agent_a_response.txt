def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obs = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]
    obstacles = set((p[0], p[1]) for p in obs)

    def man(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best_move = [0, 0]
    best_val = None
    # Evaluate "can I secure a resource this turn/soon, while denying opponent?"
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # If we step onto a resource (likely), prioritize strongly.
        on_resource = 0
        for rx, ry in resources:
            if rx == nx and ry == ny:
                on_resource = 1
                break

        # Choose a resource that maximizes advantage after our move, but penalize giving opponent an easy grab.
        best_adv = -10**9
        best_opp_take = 10**9
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd
            if sd == 0:
                adv += 5  # step-in grab
            if od < best_opp_take:
                best_opp_take = od
            if adv > best_adv:
                best_adv = adv

        # Deny: if there exists some resource opponent can reach very quickly, reduce desirability.
        deny = 0
        # Compute opponent's best grab distance among resources in 1-2 steps
        for rx, ry in resources:
            if man(ox, oy, rx, ry) <= 2:
                deny = 1
                break

        # Prefer moving toward resources closer than opponent, and when contested, bias to the nearest "blocking" direction:
        val = (on_resource * 1000
               + best_adv * 20
               - best_opp_take * 1.5
               - deny * 8
               + (man(nx, ny, ox, oy) * 0.1))  # slight separation from opponent
        # Deterministic tie-break: prefer moves in a fixed order (upper-left to lower-right as listed already)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move