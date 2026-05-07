def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obst = set()
    for a in obstacles:
        try:
            x, y = a
            obst.add((int(x), int(y)))
        except Exception:
            pass

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_move = [0, 0]
    best_val = -10**18

    has_res = len(resources) > 0
    center = (w // 2, h // 2)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obst:
            continue

        if not has_res:
            # If no visible resources, move to reduce being cornered: head toward center while biasing away from opponent.
            val = -dist((nx, ny), (ox, oy)) * 2 + dist((nx, ny), center)
        else:
            cur = (nx, ny)
            best_res_score = -10**18
            for r in resources:
                try:
                    rx, ry = r
                except Exception:
                    continue
                res = (int(rx), int(ry))
                # Race condition: prefer resources where we are significantly closer than opponent.
                self_d = dist(cur, res)
                opp_d = dist((ox, oy), res)
                # Penalize long walks from current cell; reward being earlier.
                race = (opp_d - self_d) * 5
                walk = -self_d
                # Light tie-break: prefer resources that are not behind obstacles by discouraging adjacency to obstacles near next cell.
                adj_obst = 0
                for ddx in (-1, 0, 1):
                    for ddy in (-1, 0, 1):
                        tx, ty = nx + ddx, ny + ddy
                        if (tx, ty) in obst:
                            adj_obst += 1
                tie = -adj_obst
                best_res_score = max(best_res_score, race + walk + tie)
            # If no resource offers advantage, prioritize staying safer by increasing distance from opponent and moving toward center.
            if best_res_score < 0:
                val = best_res_score + dist(cur, center) - dist(cur, (ox, oy))
            else:
                val = best_res_score - dist(cur, (ox, oy)) // 2
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move