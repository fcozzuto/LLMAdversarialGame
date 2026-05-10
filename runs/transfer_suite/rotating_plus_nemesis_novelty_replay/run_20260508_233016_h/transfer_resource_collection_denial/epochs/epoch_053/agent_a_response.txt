def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]
    obs = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                pass
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Greedy-next: after our move, maximize our lead on a resource we can reasonably "race" for.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        # If we land on a resource, that's usually best.
        landed = None
        for r in resources:
            if r[0] == nx and r[1] == ny:
                landed = r
                break

        # Choose the resource that gives best expected lead advantage after our move.
        # Add a small tie-break for resources closer to us (to finish earlier).
        best_r = None
        best_key = None
        for rx, ry in resources:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)

            # Approximate opponent "step": if we're already closer, assume opponent needs to catch up.
            # If we're behind, discourage resources where opponent is much closer (denier behavior).
            lead = opd - myd  # positive => we are closer
            key = (-abs(lead), -lead, myd, opd, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_r = (rx, ry)

        rx, ry = best_r
        myd = man(nx, ny, rx, ry)
        opd = man(ox, oy, rx, ry)
        lead = opd - myd

        # If opponent is significantly closer to the chosen resource, prefer moving toward any resource
        # where we are at least not worse (local re-target via landed preference).
        # Deterministic robustness: incorporate count of resources where we are closer after move.
        closer_cnt = 0
        for rr in resources:
            if man(nx, ny, rr[0], rr[1]) <= man(ox, oy, rr[0], rr[1]):
                closer_cnt += 1

        landed_bonus = -10 if landed is not None else 0
        # Higher closer_cnt and higher lead are better; also prefer finishing sooner (smaller myd).
        score = (-(closer_cnt), -(lead), myd, landed_bonus, dx, dy)
        if best is None or score < best[0]:
            best = (score, [dx, dy])

    return best[1]