def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = int(observation.get("grid_width", 8))
    gh = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < gw and 0 <= py < gh:
                obs.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < gw and 0 <= ry < gh and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def best_target_for(pos_self):
        # Choose a resource to maximize race against opponent while staying safe.
        best = None
        bestv = -10**18
        for t in resources:
            dS = dist(pos_self, t)
            dO = dist((ox, oy), t)
            # Prefer grabbing soon and denying: positive when we are closer than opponent.
            race = dO - dS
            # Small preference for closer absolute objective to avoid drifting.
            absd = -0.05 * dS
            v = race + absd
            if best is None or v > bestv or (v == bestv and (t[0], t[1]) < (best[0], best[1])):
                bestv = v
                best = t
        return best, bestv

    best_move = (0, 0)
    best_val = -10**18

    # If opponent is very close to any resource, we bias toward that resource (deny).
    # Determine closest resource for opponent deterministically.
    opp_target = min(resources, key=lambda t: (dist((ox, oy), t), t[0], t[1]))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < gw and 0 <= ny < gh):
            continue
        if (nx, ny) in obs:
            continue

        pos = (nx, ny)
        target, _ = best_target_for(pos)
        dS = dist(pos, target)
        dO = dist((ox, oy), target)

        # Denial bonus if targeting opponent's closest resource.
        deny = 0.0
        if target == opp_target:
            deny = 2.0

        # Safety: avoid moving too close to opponent unless we are winning the race.
        dOpp = dist(pos, (ox, oy))
        safety = 0.0
        if dOpp <= 1:
            safety = -1.5
        elif dOpp == 2:
            safety = -0.5

        # One-step look: if opponent can immediately steal opponent_target, get there first or move away.
        opp_immediate = dist((ox, oy), opp_target) <= 1
        steal_risk = 0.0
        if opp_immediate and target == opp_target and dS > 1:
            steal_risk = -3.0

        val = (dO - dS) + deny - 0.03 * dS + safety + steal_risk

        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]